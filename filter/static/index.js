/* function processForm() {
  //第一組參數
  const timeInterval_1 = document.getElementById("time-interval-1").value;
  const MA1_1 = document.getElementById("MA1-1").value;
  const comparisonOperator1_1 = document.getElementById(
    "comparison-operator-1-1"
  ).value;
  const MA1_2 = document.getElementById("MA1-2").value;
  const logicalOperator_1 = document.getElementById("logical-operator-1").value;
  const MA1_3 = document.getElementById("MA1-3").value;
  const comparisonOperator1_2 = document.getElementById(
    "comparison-operator-1-2"
  ).value;
  const MA1_4 = document.getElementById("MA1-4").value;
  //第二組參數
  const timeInterval_2 = document.getElementById("time-interval-2").value;
  const MA2_1 = document.getElementById("MA2-1").value;
  const comparisonOperator2_1 = document.getElementById(
    "comparison-operator-2-1"
  ).value;
  const MA2_2 = document.getElementById("MA2-2").value;
  const logicalOperator_2 = document.getElementById("logical-operator-2").value;
  const MA2_3 = document.getElementById("MA2-3").value;
  const comparisonOperator2_2 = document.getElementById(
    "comparison-operator-2-2"
  ).value;
  const MA2_4 = document.getElementById("MA2-4").value;
  //第三組參數
  const timeInterval_3 = document.getElementById("time-interval-3").value;
  const MA3_1 = document.getElementById("MA3-1").value;
  const comparisonOperator3_1 = document.getElementById(
    "comparison-operator-3-1"
  ).value;
  const MA3_2 = document.getElementById("MA3-2").value;
  const logicalOperator_3 = document.getElementById("logical-operator-3").value;
  const MA3_3 = document.getElementById("MA3-3").value;
  const comparisonOperator3_2 = document.getElementById(
    "comparison-operator-3-2"
  ).value;
  const MA3_4 = document.getElementById("MA3-4").value;
  //第四組參數
  const timeInterval_4 = document.getElementById("time-interval-4").value;
  const MA4_1 = document.getElementById("MA4-1").value;
  const comparisonOperator4_1 = document.getElementById(
    "comparison-operator-4-1"
  ).value;
  const MA4_2 = document.getElementById("MA4-2").value;
  const logicalOperator_4 = document.getElementById("logical-operator-4").value;
  const MA4_3 = document.getElementById("MA4-3").value;
  const comparisonOperator4_2 = document.getElementById(
    "comparison-operator-4-2"
  ).value;
  const MA4_4 = document.getElementById("MA4-4").value;

  console.log("第一组参数：");
  console.log("時間週期：" + timeInterval_1);
  console.log("MA參數一：" + MA1_1);
  console.log("比較運算符一：" + comparisonOperator1_1);
  console.log("MA參數二：" + MA1_2);
  console.log("邏輯運算符：" + logicalOperator_1);
  console.log("MA參數三：" + MA1_3);
  console.log("比較運算符二：" + comparisonOperator1_2);
  console.log("MA參數四：" + MA1_4);

  console.log("第二组参数：");
  console.log("時間週期：" + timeInterval_2);
  console.log("MA參數一：" + MA2_1);
  console.log("比較運算符一：" + comparisonOperator2_1);
  console.log("MA參數二：" + MA2_2);
  console.log("邏輯運算符：" + logicalOperator_2);
  console.log("MA參數三：" + MA2_3);
  console.log("比較運算符二：" + comparisonOperator2_2);
  console.log("MA參數四：" + MA2_4);

  console.log("第三组参数：");
  console.log("時間週期：" + timeInterval_3);
  console.log("MA參數一：" + MA3_1);
  console.log("比較運算符一：" + comparisonOperator3_1);
  console.log("MA參數二：" + MA3_2);
  console.log("邏輯運算符：" + logicalOperator_3);
  console.log("MA參數三：" + MA3_3);
  console.log("比較運算符二：" + comparisonOperator3_2);
  console.log("MA參數四：" + MA3_4);

  console.log("第四组参数：");
  console.log("時間週期：" + timeInterval_4);
  console.log("MA參數一：" + MA4_1);
  console.log("比較運算符一：" + comparisonOperator4_1);
  console.log("MA參數二：" + MA4_2);
  console.log("邏輯運算符：" + logicalOperator_4);
  console.log("MA參數三：" + MA4_3);
  console.log("比較運算符二：" + comparisonOperator4_2);
  console.log("MA參數四：" + MA4_4);
} */

function processForm() {
  const intervalData = [];

  const parameterGroups = 4;

  for (let i = 1; i <= parameterGroups; i++) {
    const timeInterval = document.getElementById(`time-interval-${i}`).value;
    const maParameters = [];
    const comparisonOperator = [];
    const logicalOperator = document.getElementById(
      `logical-operator-${i}`
    ).value;

    for (let j = 1; j <= 4; j++) {
      const maParamValue = document.getElementById(`MA${i}-${j}`).value;
      // 轉換為整數，否則為null
      const maParam = maParamValue ? parseInt(maParamValue) : null;
      maParameters.push({
        value: maParam,
      });
    }

    for (let j = 1; j <= 2; j++) {
      comparisonOperator.push({
        comparisonOperator: document.getElementById(
          `comparison-operator-${i}-${j}`
        ).value,
      });
    }

    intervalData.push({
      time_interval: timeInterval,
      param_1: maParameters[0].value,
      param_2: maParameters[1].value,
      param_3: maParameters[2].value,
      param_4: maParameters[3].value,
      comparison_operator_1: comparisonOperator[0].comparisonOperator,
      comparison_operator_2: comparisonOperator[1].comparisonOperator,
      logical_operator: logicalOperator,
    });

    //console.log(intervalData);
  }

  fetch("/add_intervals", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(intervalData),
  })
    .then((response) => response.json())
    .then((data) => {
      const messageElement = document.getElementById("message");

      messageElement.innerHTML = "";

      if (data.message.length === 0) {
        const noDataElement = document.createElement("div");
        noDataElement.textContent = "查無任何標的";
        messageElement.appendChild(noDataElement);
      } else {
        console.log(data.message);

        data.message.forEach((item) => {
          const newItemElement = document.createElement("div");
          newItemElement.innerHTML = `標的：${item["標的"]}，成交量：${item["成交量"]}`;
          messageElement.appendChild(newItemElement);
        });
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
