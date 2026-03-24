package com.challenge.day3.dto;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * Response returned by the /api/ai/chat endpoint.
 *
 * Fields:
 *  - question   : Echoed back so the client knows what was asked
 *  - answer     : OpenAI's response text
 *  - modelUsed  : Which GPT model answered (from properties)
 *  - respondedAt: Server timestamp of when response was built
 */
@Data
@Builder
public class ChatResponse {

    private String question;
    private String answer;
    private String modelUsed;
    private LocalDateTime respondedAt;
}
