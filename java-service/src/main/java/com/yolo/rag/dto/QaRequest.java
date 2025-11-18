package com.yolo.rag.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class QaRequest {

    @NotBlank(message = "Question is required")
    private String question;

    @NotEmpty(message = "At least one document ID is required")
    private List<Long> documentIds;
}
