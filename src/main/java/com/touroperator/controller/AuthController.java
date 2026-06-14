package com.touroperator.controller;

import com.touroperator.util.JwtUtil;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @PostMapping("/login")
    public Map<String, String> login(@RequestBody Map<String, String> credentials) {
        String username = credentials.get("username");
        String password = credentials.get("password");
        if ("admin".equals(username) && "admin123".equals(password)) {
            String token = JwtUtil.generateToken(username);
            return Map.of("token", token);
        }
        throw new RuntimeException("Invalid credentials");
    }
}
