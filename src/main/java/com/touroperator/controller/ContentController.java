package com.touroperator.controller;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.touroperator.util.JwtUtil;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.io.*;
import java.nio.file.*;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/content")
public class ContentController {

    private static final String CONTENT_PATH = "data/content.json";
    private static final ObjectMapper mapper = new ObjectMapper();

    @GetMapping
    public String getContent() throws IOException {
        return Files.readString(Path.of(CONTENT_PATH));
    }

    @GetMapping("/destination")
    public ResponseEntity<Map<String, String>> getDestinationByName(@RequestParam String name) throws IOException {
        JsonNode root = mapper.readTree(Path.of(CONTENT_PATH).toFile());
        String contact = root.path("contact").asText();

        for (JsonNode dest : root.path("destinations")) {
            if (dest.path("name").asText().equalsIgnoreCase(name)) {
                Map<String, String> result = new HashMap<>();
                result.put("name", dest.path("name").asText());
                result.put("price", dest.path("price").asText());
                result.put("contact", contact);
                return ResponseEntity.ok(result);
            }
        }
        return ResponseEntity.notFound().build();
    }

    @PostMapping("/update")
    public String updateContent(@RequestHeader("Authorization") String token,
                                @RequestBody String newContent) throws IOException {
        String jwt = token.replace("Bearer ", "");
        if (!JwtUtil.validateToken(jwt)) {
            throw new RuntimeException("Invalid token");
        }
        Files.writeString(Path.of(CONTENT_PATH), newContent);
        return "Content updated successfully.";
    }
}
