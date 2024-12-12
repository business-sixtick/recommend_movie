package com.recommend.movie.springbootdeveloper.service;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import com.recommend.movie.springbootdeveloper.domain.User;
import com.recommend.movie.springbootdeveloper.dto.AddUserRequest;
import com.recommend.movie.springbootdeveloper.repository.UserRepository;

import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@Service
public class UserService {
    private final UserRepository userRepository;
    private final BCryptPasswordEncoder bCryptPasswordEncoder;

    //회원 정보 추가 메서드
    public Long save(AddUserRequest dto){
        return userRepository.save(User.builder()
                .email(dto.getEmail())
                .password(bCryptPasswordEncoder.encode(dto.getPassword()))
                .build()).getId();
    }

    public User findById(Long userId){
        return userRepository.findById(userId) //유저 아이디로 유저 검색하기기
            .orElseThrow(() -> new IllegalArgumentException("unexpected user"));
    }
}
