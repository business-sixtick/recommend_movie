package com.recommend.movie.springbootdeveloper.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.recommend.movie.springbootdeveloper.domain.User;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
}