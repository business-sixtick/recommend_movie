package com.recommend.movie.springbootdeveloper.domain;

import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@EntityListeners(AuditingEntityListener.class) // 엔티티 변경 시간 체크
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED) // 프로텍티드 기본 생성자
@Table(name = "article")  // 테이블 이름을 명시적으로 지정
public class Article {
//    public class Article implements Comparable<me.shinsunyoung.blog.domain.Article>{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY) // 1씩 자동 증가
    @Column(name = "id", updatable = false)
    private Long id;

    @Column(name = "title", nullable = false)
    private String title;

    @Column(name = "content", nullable = false)
    private String content;

    @CreatedDate // 엔티티 생성 시간 저장
    @Column(name="created_at")
    private LocalDateTime createdAt;

    @LastModifiedDate // 엔티티 수정 시간 저장
    @Column(name="updated_at")
    private LocalDateTime updatedAt;

    @Builder // 빌더 패턴으로 객체 생성??
    public Article(String title, String content){
        this.title = title;
        this.content = content;
    }

    public void update(String title, String content){
        this.title = title;
        this.content = content;
    }
}