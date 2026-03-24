package com.challenge.day3.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * Request body sent by the client to the /api/ai/chat endpoint.
 *
 * Fields:
 *  - question          : The user's actual question (required)
 *  - systemInstruction : Optional — controls AI personality/role for this request
 *
 * Example body:
 * {
 *   "question": "What is a Java Stream?",
 *   "systemInstruction": "Reply like you are teaching a 10-year-old"
 * }
 */
@Data
public class ChatRequest {

    @NotBlank(message = "Question cannot be blank")
    @Size(max = 2000, message = "Question too long — max 2000 characters")
    private String question;

    // Optional field — if null or blank, ChatService uses its DEFAULT_SYSTEM_INSTRUCTION
    private String systemInstruction;
}
