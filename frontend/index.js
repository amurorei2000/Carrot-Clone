const calcTime = (timeStamp) => {
  // 한국 시간 = UTC 시간 + 9시간
  const curTime = new Date().getTime() - 9 * 60 * 60 * 1000;
  const elapsedTime = new Date(curTime - timeStamp);
  const hours = elapsedTime.getHours();
  const minutes = elapsedTime.getMinutes();
  const seconds = elapsedTime.getSeconds();

  if (hours > 0) {
    return `${hours}시간 전`;
  } else if (minutes > 0) {
    return `${minutes}분 전`;
  } else if (seconds > 0) {
    return `${seconds}초 전`;
  } else {
    return "방금 전";
  }
};

const renderData = (data) => {
  const main = document.querySelector("main");

  // 시간 역순으로 리스트 뒤집기 + db에서 받은 데이터로 화면에 그리기
  data.reverse().forEach(async (obj) => {
    // 화면 엘리멘트 생성
    const itemListDiv = document.createElement("div");
    itemListDiv.className = "item-list";

    const itemListImage = document.createElement("div");
    itemListImage.className = "item-list__img";

    const image = document.createElement("img");

    // image byte를 blob url로 가져오기
    // db에서 이미지 바이트 받기
    const res = await fetch(`/images/${obj.id}`);

    // byte array를 blob으로 변환하기
    const blob = await res.blob();

    // blob url 생성
    const url = URL.createObjectURL(blob);
    // console.log(url);
    image.src = url;
    image.alt = "image";

    const itemListInfoDiv = document.createElement("div");
    itemListInfoDiv.className = "item-list__info";

    const itemListTitleDiv = document.createElement("div");
    itemListTitleDiv.className = "item-list__info-title";
    itemListTitleDiv.innerText = obj.title;

    const itemListMetaDiv = document.createElement("div");
    itemListMetaDiv.className = "item-list__info-meta";

    const duration = calcTime(obj.insertAt);
    itemListMetaDiv.innerText = `${obj.place} ${duration}`;

    const itemListPriceDiv = document.createElement("div");
    itemListPriceDiv.className = "item-list__info-price";
    itemListPriceDiv.innerText = obj.price;

    // 조립하기
    itemListImage.appendChild(image);
    itemListDiv.appendChild(itemListImage);

    itemListInfoDiv.appendChild(itemListTitleDiv);
    itemListInfoDiv.appendChild(itemListMetaDiv);
    itemListInfoDiv.appendChild(itemListPriceDiv);
    itemListDiv.appendChild(itemListInfoDiv);

    main.appendChild(itemListDiv);
  });
};

const fetchList = async () => {
  const res = await fetch("/items");
  const data = await res.json();

  renderData(data);
};

fetchList();
