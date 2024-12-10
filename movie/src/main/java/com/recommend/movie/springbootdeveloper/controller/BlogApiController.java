package com.recommend.movie.springbootdeveloper.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.recommend.movie.springbootdeveloper.domain.Article;
import com.recommend.movie.springbootdeveloper.dto.AddArticleRequest;
import com.recommend.movie.springbootdeveloper.dto.ArticleResponse;
import com.recommend.movie.springbootdeveloper.service.BlogService;

import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
@RestController // HTTP Response Body 에 객체 데이터를 JSON 형식으로 반환하는 컨트롤러
public class BlogApiController {

    private final BlogService blogService;

    @PostMapping("/api/articles")
    public ResponseEntity<Article> addArticle(@RequestBody AddArticleRequest request){
        Article savedArticle = blogService.save(request);

        // 요청한 자원이 성공적으로 생성되었으며 저장된 블로그 글 정보를 응답 객체에 담아 전송
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(savedArticle);
    }

    @GetMapping("/api/articles")
    public ResponseEntity<List<ArticleResponse>> findAllArticles(){
        List<ArticleResponse> articles = blogService.findAll()
                .stream()  // 데이터 처리기 자바 8에서 추가됨. 데이터를 수정하지 않음. 어떤 흐름,, 참조 리스트?? 를 만듬
                .map(ArticleResponse::new)
                .toList();
        // list.forEach(item -> System.out.println(item));
        // list.forEach(System.out::println);
        // :: 연산자는 람다 축약형이라고 보임. 해당 객체의 어떤 메서드를 참조하는 연산자인거 같음.
        // ArticleResponse::new 는 생성자를 참조함. 전달인자를 생성자에 주입한다는거와 같음. 결론은 전달인자를 받아서 생성자를 호출한거임.
        // ::의 공식적인 이름은 **"메서드 참조 연산자(Method Reference Operator)"**입니다.
        return ResponseEntity.ok().body(articles);
    }

    @GetMapping("/api/articles/{id}")
    public ResponseEntity<ArticleResponse> findArticle(@PathVariable long id){
        Article article = blogService.findById(id);

        return ResponseEntity.ok().body(new ArticleResponse(article));
    }

    @DeleteMapping("/api/articles/{id}")
    public ResponseEntity<Void> deleteArticle(@PathVariable long id){
        blogService.delete(id);
        return ResponseEntity.ok().build();
    }
}
