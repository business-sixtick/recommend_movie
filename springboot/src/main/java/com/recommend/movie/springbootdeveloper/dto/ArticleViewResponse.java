package com.recommend.movie.springbootdeveloper.dto;

import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

import com.recommend.movie.springbootdeveloper.domain.Article;

@NoArgsConstructor // 기본생성자
@Getter
public class ArticleViewResponse {
    private Long id;
    private String title; // 아 리스트 디티오에서는 final 쓰고 여기서 안쓰는게 여기서는 변경을 염두해두고 안쓰는구만 ㅋ
    private String content;
    private LocalDateTime createdAt;

    public ArticleViewResponse(Article article){
        this.id = article.getId();
        this.title = article.getTitle();
        this.content = article.getContent();
        this.createdAt = article.getCreatedAt();
    }
}
