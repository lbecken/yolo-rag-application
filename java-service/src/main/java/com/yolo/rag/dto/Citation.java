package com.yolo.rag.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Citation {

    private Long chunkId;
    private String docTitle;
    private Integer pageStart;
    private Integer pageEnd;
}
