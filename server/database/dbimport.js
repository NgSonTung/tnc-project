// import * as dotenv from "dotenv"
const dotenv = require("dotenv");
const sql = require("mssql");
dotenv.config({
  path: "../config.env",
});

const dbConfig = require("./dbconfig");
const appPool = new sql.ConnectionPool(dbConfig.sqlConfig);

const fs = require("fs");
const ProductDAO = require("../DAO/ProductDAO");
const UserDAO = require("../DAO/UserDAO");
const FeatureDAO = require("../DAO/FeatureDAO");
const RatingDAO = require("../DAO/RatingDAO");
const OrderDAO = require("../DAO/OrderDAO");
const SubImageDAO = require("../DAO/SubImageDAO");
const CategoryDAO = require("../DAO/CategoryDAO");
const BrandDAO = require("../DAO/BrandDAO");
const PaymentDAO = require("../DAO/PaymentDAO");
const StatusDAO = require("../DAO/StatusDAO");
const AuthDAO = require("../DAO/AuthDAO");

const DTOProduct = require("../DTO/Default/DTOProduct");
const DTOCategory = require("../DTO/Default/DTOCategory");
const DTOBrand = require("../DTO/Default/DTOBrand");
const DTOUser = require("../DTO/Default/DTOUser");
const DTOFeature = require("../DTO/Default/DTOFeature");
const DTORating = require("../DTO/Default/DTORating");
const DTOSubImg = require("../DTO/Default/DTOSubImg");
const DTOOrder = require("../DTO/Default/DTOOrder");
const DTOOrderDetails = require("../DTO/Default/DTOOrderDetails");
const DTOLS_Status = require("../DTO/Default/DTOLS_Status");
const DTOPayment = require("../DTO/Default/DTOPayment");
const DTOAuth = require("../DTO/Default/DTOAuth");

async function importDB() {
  const PRODUCT_FILE_PATH = "../data/products.json";
  const USER_FILE_PATH = "../data/users.json";
  const FEATURE_FILE_PATH = "../data/feature.json";
  const RATING_FILE_PATH = "../data/ratings.json";
  const SUBIMAGE_FILE_PATH = "../data/subImage.json";
  const CATEGORY_FILE_PATH = "../data/category.json";
  const BRAND_FILE_PATH = "../data/brand.json";
  const ORDERS_FILE_PATH = "../data/orders.json";
  const ORDER_DETAILS_FILE_PATH = "../data/order_details.json";
  const PAYMENT_FILE_PATH = "../data/payment.json";
  const STATUS_FILE_PATH = "../data/status.json";
  const AUTH_FILE_PATH = "../data/auth.json";

  let products = JSON.parse(fs.readFileSync(PRODUCT_FILE_PATH, "utf-8"));
  let users = JSON.parse(fs.readFileSync(USER_FILE_PATH, "utf-8"));
  let features = JSON.parse(fs.readFileSync(FEATURE_FILE_PATH, "utf-8"));
  let ratings = JSON.parse(fs.readFileSync(RATING_FILE_PATH, "utf-8"));
  let orders = JSON.parse(fs.readFileSync(ORDERS_FILE_PATH, "utf-8"));
  let payments = JSON.parse(fs.readFileSync(PAYMENT_FILE_PATH, "utf-8"));
  let ls_Status = JSON.parse(fs.readFileSync(STATUS_FILE_PATH, "utf-8"));
  let auths = JSON.parse(fs.readFileSync(AUTH_FILE_PATH, "utf-8"));

  let order_details = JSON.parse(
    fs.readFileSync(ORDER_DETAILS_FILE_PATH, "utf-8")
  );
  let imgs = JSON.parse(fs.readFileSync(SUBIMAGE_FILE_PATH, "utf-8"));
  let categorys = JSON.parse(fs.readFileSync(CATEGORY_FILE_PATH, "utf-8"));
  let brands = JSON.parse(fs.readFileSync(BRAND_FILE_PATH, "utf-8"));

  //import auth
  for (let i = 0; i < auths.length; i++) {
    let auth = new DTOAuth(auths[i]);
    try {
      await AuthDAO.addAuth(auth);
      console.log("import auth --- done!");
    } catch (error) {
      throw error;
    }
  }

  //import category
  for (let i = 0; i < categorys.length; i++) {
    let category = new DTOCategory(categorys[i]);
    try {
      await CategoryDAO.addCateIfNotExists(category);
      console.log("import category --- done!");
    } catch (error) {
      throw error;
    }
  }
  //import brand
  for (let i = 0; i < brands.length; i++) {
    let brand = new DTOBrand(brands[i]);
    try {
      await BrandDAO.addBrandIfNotExists(brand);
      console.log("import brand --- done!");
    } catch (error) {
      throw error;
    }
  }
  //import product
  for (let i = 0; i < products.length; i++) {
    let product = new DTOProduct(products[i]);
    try {
      await ProductDAO.addProductIfNotExisted(product);
      console.log("import product --- done!");
    } catch (error) {
      throw error;
    }
  }
  //import users
  for (let i = 0; i < users.length; i++) {
    let user = new DTOUser(users[i]);
    try {
      await UserDAO.addUserIfNotExisted(user);
      console.log("import user --- done!");
    } catch (error) {
      throw error;
    }
  }
  // import feature
  for (let i = 0; i < features.length; i++) {
    let feature = new DTOFeature(features[i]);
    try {
      await FeatureDAO.addFeatureIfNotExisted(feature);
      console.log("import feature --- done!");
    } catch (Error) {
      // throw new Error("errr", feature);
    }
  }

  // import rating
  console.log(ratings.length);
  for (let i = 0; i < ratings.length; i++) {
    let rating = new DTORating(ratings[i]);
    // let rating = ratings[i];

    try {
      await RatingDAO.addRatingIfNotExisted(rating);
      console.log("import rating --- done!");
    } catch (Error) {
      throw Error;
    }
  }

  //import payment

  for (let i = 0; i < payments.length; i++) {
    let payment = new DTOPayment(payments[i]);

    await PaymentDAO.addPaymentIfNotExists(payment);
    try {
      console.log("import payment --- done!");
    } catch (Error) {
      throw Error;
    }
  }

  //import status

  for (let i = 0; i < ls_Status.length; i++) {
    let status = new DTOLS_Status(ls_Status[i]);

    await StatusDAO.addStatusIfNotExists(status);
    try {
      console.log("import status --- done!");
    } catch (Error) {
      throw Error;
    }
  }

  //import orders

  for (let i = 0; i < orders.length; i++) {
    let order = new DTOOrder(orders[i]);
    await OrderDAO.addOrder(order);
    try {
      console.log("import order --- done!");
    } catch (Error) {
      throw Error;
    }
  }

  //import order_details

  for (let i = 0; i < order_details.length; i++) {
    let item = new DTOOrderDetails(order_details[i]);
    try {
      await OrderDAO.addOrder_DetailsIfNotExisted(item);
      console.log("import order_details --- done!");
    } catch (Error) {
      throw Error;
    }
  }
  //import subimg
  for (let i = 0; i < imgs.length; i++) {
    let img = new DTOSubImg(imgs[i]);
    try {
      await SubImageDAO.addSubImageIfNotExisted(img);
      console.log("import subImage --- done!");
    } catch (Error) {
      throw Error;
    }
  }
  //clean refresh token in token table
  try {
    await AuthDAO.cleanRToken();
  } catch (e) {
    throw e;
  }
}

async function dbClean() {
  await AuthDAO.cleanRToken();
  await FeatureDAO.clearAll();
  await RatingDAO.clearAll();
  await SubImageDAO.clearAll();
  await OrderDAO.clearAllOrder_Details();
  await OrderDAO.clearAllOrder();
  await UserDAO.clearAll();
  await PaymentDAO.clearAll();
  await ProductDAO.clearAll();
  await CategoryDAO.clearAll();
  await BrandDAO.clearAll();
  await StatusDAO.clearAll();
  await AuthDAO.clearAll();
}
appPool
  .connect()
  .then(async function (pool) {
    dbConfig.db.pool = pool;
    console.log("SQL Connected!");

    if (process.argv[2] === "--clean") {
      console.log("cleaning db ...");
      await dbClean();
    } else if (process.argv[2] === "--import") {
      console.log("should import");
      await importDB();
    }
    console.log("ALL DONE !!!");
  })
  .catch(function (err) {
    console.error("Error creating db connection pool", err);
  });
