package com.rag.app.service;

import com.rag.app.client.EmbeddingClient;
import com.rag.app.dto.Citation;
import com.rag.app.dto.QaResponse;
import com.rag.app.model.Chunk;
import com.rag.app.repository.ChunkRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.messages.Message;
import org.springframework.ai.chat.messages.SystemMessage;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class QaService {

    private static final Logger logger = LoggerFactory.getLogger(QaService.class);

    private final EmbeddingClient embeddingClient;
    private final ChunkRepository chunkRepository;
    private final ChatClient chatClient;
    private final int topK;

    private static final String SYSTEM_PROMPT = """
            You are a helpful assistant that answers questions based ONLY on the provided context.

            Important instructions:
            - Use ONLY the information from the context below to answer the question.
            - If the answer is not in the context, say "I don't have enough information in the provided documents to answer this question."
            - Do not make up information or use knowledge outside of the provided context.
            - Be concise and direct in your answers.
            - If you quote from the context, indicate which source you are using.
            """;

    public QaService(
            EmbeddingClient embeddingClient,
            ChunkRepository chunkRepository,
            ChatClient.Builder chatClientBuilder,
            @Value("${rag.retrieval.top-k:5}") int topK) {
        this.embeddingClient = embeddingClient;
        this.chunkRepository = chunkRepository;
        this.chatClient = chatClientBuilder.build();
        this.topK = topK;
    }

    /**
     * Answer a question using RAG pipeline.
     *
     * @param question    The user's question
     * @param documentIds List of document IDs to search within
     * @return QaResponse with answer and citations
     */
    public QaResponse answerQuestion(String question, List<Long> documentIds) {
        logger.info("Processing question: {}", question);
        logger.info("Searching in documents: {}", documentIds);

        // Step 1: Get query embedding
        float[] embedding = embeddingClient.embedSingle(question);
        String queryEmbedding = EmbeddingClient.toPgVectorFormat(embedding);
        logger.debug("Generated query embedding");

        // Step 2: Retrieve top-k nearest chunks
        List<Chunk> relevantChunks = chunkRepository.findNearestChunks(
                documentIds,
                queryEmbedding,
                topK
        );
        logger.info("Retrieved {} relevant chunks", relevantChunks.size());

        if (relevantChunks.isEmpty()) {
            return QaResponse.builder()
                    .answer("No relevant content found in the specified documents.")
                    .citations(new ArrayList<>())
                    .build();
        }

        // Step 3: Build context from chunks
        String context = buildContext(relevantChunks);
        logger.debug("Built context with {} characters", context.length());

        // Step 4: Build citations
        List<Citation> citations = buildCitations(relevantChunks);

        // Step 5: Call LLM with prompt
        String answer = callLlm(context, question);
        logger.info("Generated answer with {} characters", answer.length());

        return QaResponse.builder()
                .answer(answer)
                .citations(citations)
                .build();
    }

    /**
     * Build context string from retrieved chunks.
     */
    private String buildContext(List<Chunk> chunks) {
        StringBuilder context = new StringBuilder();

        for (int i = 0; i < chunks.size(); i++) {
            Chunk chunk = chunks.get(i);
            String docTitle = chunk.getDocument() != null ?
                    chunk.getDocument().getTitle() : "Unknown Document";

            context.append(String.format("--- Source %d: %s (Pages %d-%d) ---\n",
                    i + 1,
                    docTitle,
                    chunk.getPageStart(),
                    chunk.getPageEnd()));
            context.append(chunk.getText());
            context.append("\n\n");
        }

        return context.toString();
    }

    /**
     * Build citations from chunks.
     */
    private List<Citation> buildCitations(List<Chunk> chunks) {
        List<Citation> citations = new ArrayList<>();

        for (Chunk chunk : chunks) {
            String docTitle = chunk.getDocument() != null ?
                    chunk.getDocument().getTitle() : "Unknown Document";

            citations.add(Citation.builder()
                    .chunkId(chunk.getId())
                    .docTitle(docTitle)
                    .pageStart(chunk.getPageStart())
                    .pageEnd(chunk.getPageEnd())
                    .build());
        }

        return citations;
    }

    /**
     * Call LLM with context and question.
     */
    private String callLlm(String context, String question) {
        String userPrompt = String.format("""
                Context:
                %s

                Question: %s

                Please answer the question based only on the context provided above.
                """, context, question);

        try {
            List<Message> messages = List.of(
                    new SystemMessage(SYSTEM_PROMPT),
                    new UserMessage(userPrompt)
            );

            String response = chatClient.prompt(new Prompt(messages))
                    .call()
                    .content();

            return response != null ? response : "Unable to generate an answer.";
        } catch (Exception e) {
            logger.error("Error calling LLM: {}", e.getMessage());
            throw new RuntimeException("Failed to get response from LLM", e);
        }
    }
}
