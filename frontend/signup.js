const form = document.querySelector("#signup-form");
const infoDiv = document.getElementById("info");

const checkPassword = () => {
  const formData = new FormData(form);
  const password1 = formData.get("password");
  const password2 = formData.get("password2");

  if (password1 === password2) {
    return true;
  } else {
    return false;
  }
};

const handleSubmit = async (event) => {
  event.preventDefault();
  const formData = new FormData(form);

  // 비밀번호 암호화(sha-256)
  const sha256password = sha256(formData.get("password"));
  formData.set("password", sha256password);

  // 비밀번호와 비밀번호 확인 값이 같은지 비교
  if (checkPassword()) {
    const res = await fetch("/signup", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();

    if (data == "200") {
      //   infoDiv.innerText = "회원 가입에 성공했습니다.";
      //   infoDiv.style.color = "blue";
      alert("회원 가입에 성공했습니다.");
      window.location.pathname = "/login.html";
    }
  } else {
    infoDiv.innerText = "비밀번호가 같지 않습니다.";
    infoDiv.style.color = "red";
  }
};

form.addEventListener("submit", handleSubmit);
