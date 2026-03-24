package com.challenge.day3.service;

import com.challenge.day3.dto.ChatRequest;
import com.challenge.day3.dto.ChatResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.Optional;

/**
 * Core service that communicates with OpenAI GPT via Spring AI.
 *
 * Why Spring AI over calling OpenAI HTTP API directly?
 * - No manual HTTP client setup
 * - No JSON request/response parsing
 * - No auth header management
 * - Same code works for OpenAI, Gemini, Claude — just change the dependency!
 *
 * Spring AI auto-configures ChatModel using your application.properties API key.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ChatService {

    // Spring AI auto-wires this based on spring-ai-starter-model-openai dependency
    private final ChatModel chatModel;

    // Reads model name from application.properties — avoids hardcoding
    @Value("${spring.ai.openai.chat.options.model}")
    private String modelName;

    /**
     * Default system instruction — AI's "job description" when caller doesn't provide one.
     * Text block (Java 15+) keeps multiline strings clean and readable.
     */
    private static final String DEFAULT_SYSTEM_INSTRUCTION = """
            You are a helpful, concise Java backend assistant.
            - Give practical, real-world answers.
            - Include short code examples when relevant.
            - If you don't know something, say so honestly.
            - Keep answers clear and to the point.
            """;

    /**
     * Sends user's question to OpenAI GPT and returns a structured response.
     *
     * Flow:
     * 1. Resolve system instruction → caller's OR default (Java 8 Optional)
     * 2. Build prompt with system + user message roles
     * 3. Call OpenAI via Spring AI ChatClient (handles HTTP + auth internally)
     * 4. Wrap result in ChatResponse DTO
     *
     * @param request validated request from controller
     * @return structured ChatResponse with AI's answer
     */
    public ChatResponse chat(ChatRequest request) {

        // Java 8 Optional — null-safe fallback for systemInstruction
        String systemPrompt = Optional.ofNullable(request.getSystemInstruction())
                .filter(s -> !s.isBlank())
                .orElse(DEFAULT_SYSTEM_INSTRUCTION);

        log.info("Sending to OpenAI [model={}] | question length: {} chars",
                modelName, request.getQuestion().length());

        // Spring AI ChatClient — fluent API
        // .system() → sets AI role/personality (like giving it a job description)
        // .user()   → the actual question from end user
        // .call().content() → executes HTTP call, extracts text from response
        String answer = ChatClient.create(chatModel)
                .prompt()
                .system(systemPrompt)
                .user(request.getQuestion())
                .call()
                .content();

        log.info("Received answer from OpenAI | answer length: {} chars", answer.length());

        return ChatResponse.builder()
                .question(request.getQuestion())
                .answer(answer)
                .modelUsed(modelName)
                .respondedAt(LocalDateTime.now())
                .build();
    }
}
