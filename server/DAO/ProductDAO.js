// const products = require("../../client/src/data/products.json");
const sql = require("mssql");

const ProductSchema = require("../Model/Product");
const BrandSchema = require("../Model/Brand");
const RatingSchema = require("../Model/Rating");

const dbConfig = require("../database/dbconfig");
const dbUtils = require("../utils/dbUtils");
const DateTimeUtils = require("../utils/DateTimeUtils");
const ImageUtils = require("../utils/ImageUtils");
const StaticData = require("../utils/StaticData");

const CategoryDAO = require("./CategoryDAO");
const BrandDAO = require("./BrandDAO");
const RatingDAO = require("./RatingDAO");

const DTOProductCustomize = require("../DTO/Customize/DTOProductCustomize");
const DTOProduct = require("../DTO/Default/DTOProduct");

exports.addProductIfNotExisted = async (product) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  product.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);

  let insertData = ProductSchema.validateData(product);

  let query = `SET IDENTITY_INSERT ${ProductSchema.schemaName} ON insert into ${ProductSchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(
      ProductSchema.schema,
      dbConfig.db.pool.request(),
      insertData
    );
  if (!insertFieldNamesStr || !insertValuesStr) {
    throw new Error("Invalid insert param");
  }

  query +=
    " (" +
    insertFieldNamesStr +
    ") select  " +
    insertValuesStr +
    ` WHERE NOT EXISTS(SELECT * FROM ${ProductSchema.schemaName} WHERE name = @name)` +
    ` SET IDENTITY_INSERT ${ProductSchema.schemaName} OFF`;
  // console.log(query);

  let result = await request.query(query);

  // console.log(result);
  return result.recordsets;
};

exports.clearAll = async () => {
  query = `delete ${ProductSchema.schemaName}  DBCC CHECKIDENT ('[${ProductSchema.schemaName} ]', RESEED, 1);`;
  let result = await dbConfig.db.pool.request().query(query);
  return result.recordsets;
};

exports.getProductByName = async (name) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request
    .input(
      `${ProductSchema.schema.Name.name}`,
      ProductSchema.schema.Name.sqlType,
      name
    )
    .query(
      `select * from ${ProductSchema.schemaName} where ${ProductSchema.schema.Name.name} = @${ProductSchema.schema.Name.name}`
    );
  console.log(result);
  if (result.recordsets[0][0]) {
    return new DTOProduct(result.recordsets[0][0]);
  }
  return result.recordsets[0][0];
};

exports.getProductById = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request
    .input(
      `${ProductSchema.schema.ProductID.name}`,
      ProductSchema.schema.ProductID.sqlType,
      id
    )
    .query(
      `SELECT p.*,b.BrandName FROM ${ProductSchema.schemaName} p
       join ${BrandSchema.schemaName} b on b.brandID = p.brandID
        where ${ProductSchema.schema.ProductID.name} = @${ProductSchema.schema.ProductID.name}
       `
    );
  console.log(result.recordsets[0][0]);
  return new DTOProductCustomize(result.recordsets[0][0]);
};

exports.getAllProducts = async (reqHeader) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }

  let filter = {};
  const {categoryname, brandname, price, name, currentpage, sort} = reqHeader;

  if (price) {
    const priceArr = price.split(",");
    filter.Price = {};
    priceArr.forEach((item) => {
      const [key, value] = item.split(":");
      filter.Price[key.trim()] = parseFloat(value);
    });
  }
  if (categoryname) {
    if (categoryname.includes(",")) {
      const arr = categoryname.split(",");

      const cateIds = await Promise.all(
        arr.map(async (element) => {
          return await CategoryDAO.getCategoryIdByName(element);
        })
      );
      filter.CategoryID = cateIds;
    } else {
      filter.CategoryID = await CategoryDAO.getCategoryIdByName(categoryname);
    }
  }

  if (brandname) {
    if (brandname.includes(",")) {
      const arr = brandname.split(",");
      const brandIds = await Promise.all(
        arr.map(async (element) => {
          return await BrandDAO.getBrandIDByBrandName(element);
        })
      );
      filter.BrandID = brandIds;
    } else {
      filter.BrandID = await BrandDAO.getBrandIDByBrandName(brandname);
    }
  }

  if (name) {
    const convertedName = decodeURI(name);
    filter.Name = convertedName;
  }
  if (currentpage) {
    filter.CurrentPage = currentpage;
  }
  if (sort) {
    filter.Sort = sort;
  }
  const page = filter.CurrentPage * 1 || 1;
  let pageSize = filter.pageSize * 1 || StaticData.config.MAX_PAGE_SIZE;
  if (pageSize > StaticData.config.MAX_PAGE_SIZE) {
    pageSize = StaticData.config.MAX_PAGE_SIZE;
  }
  let selectQuery = `
  SELECT ${ProductSchema.schemaName}.*,
    ${BrandSchema.schemaName}.BrandName
    FROM ${ProductSchema.schemaName}
  join ${BrandSchema.schemaName} on ${BrandSchema.schemaName}.brandID = ${ProductSchema.schemaName}.brandID `;
  let countQuery = `SELECT COUNT(DISTINCT ${ProductSchema.schema.ProductID.name}) as totalItem from ${ProductSchema.schemaName}`;

  const dataRating = await RatingDAO.getAllRatings();

  const {filterStr, paginationStr} = dbUtils.getFilterProductsQuery(
    ProductSchema.schema,
    filter,
    page,
    pageSize,
    ProductSchema.defaultSort
  );

  // console.log(filterStr);

  if (filterStr) {
    selectQuery += " " + filterStr;
    countQuery += " " + filterStr;
  }

  if (paginationStr) {
    selectQuery += " " + paginationStr;
  }

  const result = await dbConfig.db.pool.request().query(selectQuery);
  let countResult = await dbConfig.db.pool.request().query(countQuery);
  let totalProduct = 0;
  if (countResult.recordsets[0].length > 0) {
    totalProduct = countResult.recordsets[0][0].totalItem;
  }
  let totalPage = Math.ceil(totalProduct / pageSize); //round up
  const products = result.recordsets[0];

  const productsDTO = await Promise.all(
    products.map(async (element) => {
      const converted = await ImageUtils.convertImageToBase64(element.Image);
      const productRating = dataRating.find(
        (rating) => rating.ProductID === element.ProductID
      );
      delete productRating.RatingID;
      delete productRating.ProductID;
      delete productRating.CreatedAt;
      let ratingAvg = 0;
      for (let key in productRating) {
        ratingAvg += productRating[key];
      }
      element.RatingAvg = ratingAvg / 5;
      // console.log(element);
      element.Base64Image = converted.Base64;
      return new DTOProductCustomize(element);
    })
  );

  return {
    Page: page,
    PageSize: pageSize,
    TotalPage: totalPage,
    TotalProduct: totalProduct,
    DataProducts: productsDTO,
  };
};
exports.createNewRating = async (product) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  if (!product) {
    throw new Error("Invalid input param");
  }
  let request = dbConfig.db.pool.request();
  console.log(product);
  let query = `insert into ${RatingSchema.schemaName}(${ProductSchema.schema.ProductID.name}) values(${product.ProductID})`;
  console.log(query);
  let result = await request.query(query);
  return result.recordsets;
};
exports.createNewProduct = async (product) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  if (!product) {
    throw new Error("Invalid input param");
  }
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  product.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);
  let insertData = ProductSchema.validateData(product);
  let query = `insert into ${ProductSchema.schemaName}`;
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(
      ProductSchema.schema,
      dbConfig.db.pool.request(),
      insertData
    );
  query += " (" + insertFieldNamesStr + ") values (" + insertValuesStr + ")";
  // console.log(query);
  let result = await request.query(query);
  return result.recordsets;
};

exports.deleteProductById = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request
    .input(
      `${ProductSchema.schema.ProductID.name}`,
      ProductSchema.schema.ProductID.sqlType,
      id
    )
    .query(
      `delete ${ProductSchema.schemaName} where ${ProductSchema.schema.ProductID.name} = @${ProductSchema.schema.ProductID.name}`
    );
  return result.recordsets;
};

exports.deleteMultipleProductById = async (idList) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  for (let i = 0; i < idList.length; i++) {
    ProductSchema.schema.ProductID.validate(idList[i]);
  }
  let request = dbConfig.db.pool.request();
  const deleteStr = dbUtils.getDeleteQuery(ProductSchema, idList);
  let result = await request.query(
    `DELETE FROM ${ProductSchema.schemaName} WHERE ${ProductSchema.schema.ProductID.name} ${deleteStr}`
  );
  return result.recordsets;
};

exports.updateProductById = async (id, updateInfo) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  if (!updateInfo) {
    throw new Error("Invalid input param");
  }
  // console.log(updateInfo);
  let query = `update ${ProductSchema.schemaName} set`;
  const {request, updateStr} = dbUtils.getUpdateQuery(
    ProductSchema.schema,
    dbConfig.db.pool.request(),
    updateInfo
  );
  if (!updateStr) {
    throw new Error("Invalid update param");
  }
  request.input(
    `${ProductSchema.schema.ProductID.name}`,
    ProductSchema.schema.ProductID.sqlType,
    id
  );
  query +=
    " " +
    updateStr +
    ` where ${ProductSchema.schema.ProductID.name} = @${ProductSchema.schema.ProductID.name}`;
  query += ` select * from ${ProductSchema.schemaName} where ${ProductSchema.schema.ProductID.name} = @${ProductSchema.schema.ProductID.name}`;
  let result = await request.query(query);
  return new DTOProduct(result.recordsets[0]);
};

exports.getProductsNotPagination = async () => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let request = dbConfig.db.pool.request();
  let result = await request.query(`select * from ${ProductSchema.schemaName}`);
  let dtos = result.recordsets[0].map((x) => new DTOProduct(x));
  return dtos;
};

exports.handleUpdateStock = async (element, reverse = false) => {
  const product = await this.getProductById(element.ProductID);
  console.log(product);
  await this.updateProductById(element.ProductID, {
    Stock: reverse
      ? product.Stock + element.Amount
      : product.Stock - element.Amount,
  });
};
