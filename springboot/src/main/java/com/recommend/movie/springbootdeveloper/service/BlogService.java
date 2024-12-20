package com.recommend.movie.springbootdeveloper.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.recommend.movie.springbootdeveloper.domain.Article;
import com.recommend.movie.springbootdeveloper.dto.AddArticleRequest;
import com.recommend.movie.springbootdeveloper.dto.UpdateArticleRequest;
import com.recommend.movie.springbootdeveloper.repository.BlogRepository;

import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@Service
public class BlogService {
    
    private final BlogRepository blogRepository;

    public Article save(AddArticleRequest request){
        return blogRepository.save(request.toEntity());
    }

    public List<Article> findAll(){
        return blogRepository.findAll(); //테이블에 저장되어 있는 모든 데이터 조회
    }

    public Article findById(long id){
        return blogRepository.findById(id)
        .orElseThrow(() -> new IllegalArgumentException("not found: " + id));
    }

    public void delete(long id){
        blogRepository.deleteById(id);
    }

    @Transactional //두 작업을 한 단위로 묶어서 오류 발생을 막는다
    public Article update(long id, UpdateArticleRequest request){
        Article article = blogRepository.findById(id).orElseThrow(() -> new IllegalArgumentException("not found: " + id));

        article.update(request.getTitle(), request.getContent());

        return article;
    }
}
