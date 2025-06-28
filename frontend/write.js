const form = document.getElementById("write-form");

const handleSubmitForm = async (event) => {
  // submit 리디렉션 금지
  event.preventDefault();

  // multipart-formdata 객체 작성
  const body = new FormData(form);

  // 현재 타임스탬프 추가
  body.append("insertAt", new Date().getTime());

  try {
    const res = await fetch("/items", {
      method: "POST",
      body: body,
    });

    const data = await res.json();
    if (data === "200") {
      window.location.pathname = "/";
      // console.log(data);
    }
  } catch (e) {
    console.error("이미지 업로드에 실패했습니다.");
    console.error(e);
  }
};

form.addEventListener("submit", handleSubmitForm);
