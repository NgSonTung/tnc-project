const fs = require("fs");

const json = JSON.parse(fs.readFileSync("./products.json", "utf-8"));
let data = [];
let index = 1;
json.forEach((element) => {
  var obj = {};
  Object.keys(element).forEach((i) => {
    if (i != undefined) {
      let value = element[`${i}`];
      let finalConcat = func(i, value);
      obj[finalConcat] = value;
    }
  });
  obj["StatusID"] = 1;
  data.push(obj);
  console.log("index : ", index++);
  return;
});

function func(word) {
  let firstChar = word.slice(0, 1);
  let remainWord = word.slice(1, word.length);
  let finalConcat = firstChar.toUpperCase() + remainWord;
  return finalConcat;
}

// function addMoreProps(element){
//   element[Address] ="asdadadadsadadsadasdsadsadasdsadadasdadada"
//   element[email] =""
//   element[Phone] ="0000000000"
//   element[PaymentID] ="1"
//   element[StatusID] ="1"
//   StatusID
// }

const jsonData = JSON.stringify(data, null, 2);
fs.writeFileSync("products.json", jsonData, "utf-8");
