package com.recommend.movie.springbootdeveloper.controller;

import lombok.Getter;
import lombok.Setter;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.time.LocalDate;
import java.util.List;

@Controller // 뷰, 페이지를 관리한다. /resource/templates 디렉터리에서 페이지를 찾는다.
public class ExampleController {

    @GetMapping("/thymeleaf/example")
    public String thymeleafExample(Model model){
        Person examplePerson = new Person();
        examplePerson.setId(1L);
        examplePerson.setName("cho");
        examplePerson.setAge(44);
        examplePerson.setHobbies(List.of("work", "run"));

        // model은 html로 객체를 보낼때 쓴다.
        model.addAttribute("person", examplePerson);
        model.addAttribute("today", LocalDate.now());

        return "example"; // example.html 라는 뷰 조회
    }

    @Setter
    @Getter
    class Person{
        private Long id;
        private String name;
        private int age;
        private List<String> hobbies;
    }
}
