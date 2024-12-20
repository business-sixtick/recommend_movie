package com.recommend.movie.springbootdeveloper.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import com.recommend.movie.springbootdeveloper.domain.Article;

public interface BlogRepository extends JpaRepository<Article, Long> {
    // Long 타입의 PK를 갖는 Article 매핑 테이블
}