package com.recommend.movie.springbootdeveloper.controller;
//로그인이나 가입 경로로 접근하면 뷰 파일을 관리함

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class UserViewController {

    @GetMapping("/login")
    public String login(){
        return "login";
    }

    @GetMapping("/signup")
    public String signup(){
        return "signup";
    }
}