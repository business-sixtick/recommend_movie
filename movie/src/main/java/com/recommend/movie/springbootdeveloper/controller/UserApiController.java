package com.recommend.movie.springbootdeveloper.controller;

import lombok.RequiredArgsConstructor;

import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.logout.SecurityContextLogoutHandler;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;

import com.recommend.movie.springbootdeveloper.dto.AddUserRequest;
import com.recommend.movie.springbootdeveloper.service.UserService;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@RequiredArgsConstructor
@Controller
public class UserApiController {
    private final UserService userService;

    @PostMapping("/user")
    //서비스 메서드를 사용해 사용자를 저장하고, 로그인 페이지로 리다이렉트
    public String signup(AddUserRequest request){
        userService.save(request);
        return "redirect:/login"; //처리가 끝나면 강제로 이 url로 이동한다
    }

    @GetMapping("/logout") //로그아웃 메서드
    public String logout(HttpServletRequest request, HttpServletResponse response){
        new SecurityContextLogoutHandler().logout(request, response, SecurityContextHolder.getContext().getAuthentication());
        return "redirect:/login";
    }
}
