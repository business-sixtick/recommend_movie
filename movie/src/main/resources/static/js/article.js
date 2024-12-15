const deleteButton = document.getElementById('delete-btn');

if (deleteButton){
    deleteButton.addEventListener('click', () => {
        let id = document.getElementById('article-id').value;
        fetch(`/api/articles/${id}`, {method: 'DELETE'})
        .then(() => {
            alert('삭제가 완료 되었습니다.');
            location.replace('/articles');
        });
    });
}



const modifyButton = document.getElementById('modify-btn');

if (modifyButton){
    modifyButton.addEventListener('click', () => {
        let params = new URLSearchParams(location.search);
        let id = params.get('id');

        fetch(`/api/articles/${id}`, {
            method: 'PUT',
            headers:{"Content-Type": "application/json"},
            body: JSON.stringify({
                title : document.getElementById('title').value,
                content: document.getElementById('content').value,
            })
        })
        .then(() => {
            alert('수정이 완료 되었습니다.');
            location.replace(`/articles/${id}`); //리다이렉션 주소
        });
    });
}



const createButton = document.getElementById('create-btn');

if (createButton){
    createButton.addEventListener('click', () => {

        fetch("/api/articles", {
            method: 'POST',
            headers:{"Content-Type": "application/json"},
            body: JSON.stringify({
                title : document.getElementById('title').value,
                content: document.getElementById('content').value,
            })
        })
        .then(() => {
            alert('등록이 완료 되었습니다.');
            location.replace('/articles');
        });
    });
}



function isLoggedIn() {
    return !!localStorage.getItem('accessToken'); // 토큰 존재 여부 확인
}

function logout() {
    localStorage.removeItem('accessToken'); // 토큰 삭제
    location.reload(); // 현재 페이지 새로고침
}

document.addEventListener("DOMContentLoaded", () => {
    const loginButton = document.getElementById("loginButton");
    const logoutButton = document.getElementById("logoutButton");

    if (isLoggedIn()) {
        loginButton.style.display = "none"; // 로그인 상태라면 로그인 버튼 숨김
        logoutButton.style.display = "block"; // 로그아웃 버튼 표시
    } else {
        loginButton.style.display = "block"; // 비로그인 상태라면 로그인 버튼 표시
        logoutButton.style.display = "none"; // 로그아웃 버튼 숨김
    }
});


async function login(event) {
    event.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        if (response.ok) {
            const { accessToken } = await response.json();
            localStorage.setItem('accessToken', accessToken); // 토큰 저장
            window.location.href = '/articles'; // 로그인 후 이동
        } else {
            alert('Login failed!');
        }
    } catch (error) {
        console.error('Error logging in:', error);
    }
}
