show databases;

create database movie;

use movie;

create table posters (
    id int auto-increment primary key,
	image longblob not null, 
    title varchar(255) not null,
    relYear int not null,
    rating varchar(20) not null,
    runTime float not null,
    genre varchar(255) not null,
    director varchar(255) not null,
    story varchar(2000) not null,
    actor varchar(255) not null,
    prod varchar(255) not null,
    nation varchar(255) not null,
    etc varchar(255)
);

select * from posters;

-- alter table posters
-- add column story varchar(2000) not null after actor,
-- add column relYear int not null after title,
-- add column rating varchar(20) not null after relYear,
-- add column runTime float not null after rating;


-- 기존에 존재하는 데이터베이스를 버린다  
-- drop database movie;