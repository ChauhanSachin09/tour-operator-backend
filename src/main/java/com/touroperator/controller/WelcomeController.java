package com.touroperator.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.io.IOException;


@RestController
@RequestMapping("/healthcheck")
public class WelcomeController {

    @GetMapping
    public String getHealth() throws IOException {
        return "OK";
    }
}
