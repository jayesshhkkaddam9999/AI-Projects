package com.challenge.day3.dto;

import lombok.Builder;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Standard error response returned when something goes wrong.
 * Used by GlobalExceptionHandler for all error cases.
 */
@Data
@Builder
public class ErrorResponse {

    private int status;
    private String error;
    private List<String> messages;
    private LocalDateTime timestamp;
}
