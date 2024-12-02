const express = require("express");
const cors = require("cors");
const morgan = require("morgan");
const bodyParser = require("body-parser");
const cookieParser = require("cookie-parser");
const path = require("path");

const app = express();
//The order of middleware in stack is defined by the order they are defined in the code
app.use(bodyParser.json({limit: "40mb"}));
app.use(bodyParser.urlencoded({extended: true, limit: "40mb"}));
const corsOptions = {
  origin: "http://localhost:4200",
  credentials: true, //access-control-allow-credentials:true
  optionSuccessStatus: 200,
};
app.use(cors(corsOptions));
if (process.env.NODE_ENV === "dev") {
  //3RD-party MIDDLE WARE - HTTP request logger middleware
  app.use(morgan("dev"));
}
app.use(cookieParser());
//using express.json middleware -> stand between req and response
app.use(express.json());
app.use((req, res, next) => {
  req.requestTime = new Date().toISOString();
  // console.log("request Time:", req.requestTime);
  next();
});
// app.set("view engine", "ejs");
// app.set("views", path.join(__dirname, "template"));
app.use(express.static("template"));

//method 3: mouting the router on a route
const productRouter = require("./routes/product");
const orderRouter = require("./routes/order");
const ratingRouter = require("./routes/rating");
const subimgRouter = require("./routes/subimg");
const featureRouter = require("./routes/feature");
const brandRouter = require("./routes/brand");
const categoryRouter = require("./routes/category");
// const uploadRouter = require("./routes/upload");
const userRouter = require("./routes/user");
const paymentRouter = require("./routes/payment");
const tokenRouter = require("./routes/token");
const chatbotRouter = require("./routes/chatbot");
app.use("/api/v1/product", productRouter);
app.use("/api/v1/order", orderRouter);
app.use("/api/v1/rating", ratingRouter);
app.use("/api/v1/subimg", subimgRouter);
app.use("/api/v1/feature", featureRouter);
app.use("/api/v1/user", userRouter);
app.use("/api/v1/brand", brandRouter);
app.use("/api/v1/category", categoryRouter);
app.use("/api/v1/payment", paymentRouter);
app.use("/api/v1/token", tokenRouter);
app.use("/api/v1/chatbot", chatbotRouter);

// app.use("/api/v1/upload", uploadRouter);

module.exports = app;
