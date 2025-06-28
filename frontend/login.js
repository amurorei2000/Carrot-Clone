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
  console.log(data);

  if (res.status === 200) {
    alert("로그인에 성공했습니다");
    window.location.pathname = "/";
  } else if (res.status === 401) {
    alert("아이디 혹은 패스워드가 틀렸습니다.");
  }
};

form.addEventListener("submit", handleSubmit);
