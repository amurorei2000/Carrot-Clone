const form = document.getElementById("login-form");

const handleSubmit = async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  // sha256으로 패스워드를 인코딩
  const sha256password = sha256(formData.get("password"));
  formData.set("password", sha256password);

  const res = await fetch("/login", {
    method: "POST",
    body: formData,
  });
  const data = await res.json();

  // 엑세스 토큰 저장 -> 로컬 스토리지, 세션 스토리지
  const accessToken = data.access_token;
  const refreshToken = data.refresh_token;
  window.localStorage.setItem("access_token", accessToken);
  window.localStorage.setItem("refresh_token", refreshToken);
  // window.sessionStorage.setItem("token", accessToken);

  // const infoDiv = document.getElementById("info");
  // infoDiv.innerText = "로그인 되었습니다.";
  // const infoBtn = document.createElement("button");
  // infoBtn.innerText = "상품 가져오기";
  // infoBtn.addEventListener("click", async () => {
  //   // 엑세스 토큰을 헤더에 추가
  //   const res = await fetch("/items", {
  //     headers: {
  //       Authorization: `Bearer ${accessToken}`,
  //     },
  //   });
  //   const resData = await res.json();
  //   console.log(resData);
  // });
  // infoDiv.appendChild(infoBtn);

  if (res.status === 200) {
    alert("로그인에 성공했습니다");
    window.location.pathname = "/";
  } else if (res.status === 401) {
    alert("아이디 혹은 패스워드가 틀렸습니다.");
  }
};

form.addEventListener("submit", handleSubmit);
