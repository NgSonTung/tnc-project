const dbConfig = require("../database/dbconfig");
const dbUtils = require("../utils/dbUtils");
const bcrypt = require("bcryptjs");

const StaticData = require("../utils/StaticData");
const {OrdersSchema, Order_DetailsSchema} = require("../Model/Order");
const UserSchema = require("../Model/User");
const ProductSchema = require("../Model/Product");

const DTOUser = require("../DTO/Default/DTOUser");
const DTOUserCustomize = require("../DTO/Customize/DTOUserCustomize");
const OrderDAO = require("../DAO/OrderDAO");
const DateTimeUtils = require("../utils/DateTimeUtils");

exports.addUserIfNotExisted = async (user) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  user.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);

  let insertData = UserSchema.validateData(user);
  insertData.Password = await bcrypt.hash(insertData.Password, 10);
  let query = `SET IDENTITY_INSERT ${UserSchema.schemaName} ON insert into ${UserSchema.schemaName}`;
  // schema, request, insert
  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(
      UserSchema.schema,
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
    ` WHERE NOT EXISTS(SELECT * FROM ${UserSchema.schemaName} WHERE userName = @userName)` +
    ` SET IDENTITY_INSERT ${UserSchema.schemaName} OFF`;
  let result = await request.query(query);
  return result.recordsets;
};

exports.insertUser = async (user) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  // console.log("user auth", user.auth);
  const ms = DateTimeUtils.convertDateTimeToMilliseconds(Date.now());
  user.CreatedAt = DateTimeUtils.convertMillisecondsToDateTimeSQL(ms);
  let insertData = UserSchema.validateData(user);
  insertData.password = await bcrypt.hash(insertData.Password, 10);

  let query = `insert into ${UserSchema.schemaName} `;

  const {request, insertFieldNamesStr, insertValuesStr} =
    dbUtils.getInsertQuery(
      UserSchema.schema,
      dbConfig.db.pool.request(),
      insertData
    );
  if (!insertFieldNamesStr || !insertValuesStr) {
    throw new Error("Invalid insert param");
  }
  query += " (" + insertFieldNamesStr + ") select  " + insertValuesStr;
  let result = await request.query(query);
  return result.recordsets;
};

exports.getAllUsers = async (filter) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  if (!filter.page) {
    const result = await dbConfig.db.pool
      .request()
      .query(`SELECT * FROM ${UserSchema.schemaName} `);
    return {DataUsers: result.recordsets[0]};
  }

  const page = filter.page * 1 || 1;
  let pageSize = filter.pageSize * 1 || StaticData.config.MAX_PAGE_SIZE;
  if (pageSize > StaticData.config.MAX_PAGE_SIZE) {
    pageSize = StaticData.config.MAX_PAGE_SIZE;
  }
  let selectQuery = `SELECT * FROM ${UserSchema.schemaName} `;
  let countQuery = `SELECT COUNT(DISTINCT ${UserSchema.schema.UserID.name}) as totalItem from ${UserSchema.schemaName} `;
  if (filter) {
    filter["UserID"] = {gt: "0"};
  }
  const {filterStr, paginationStr} = dbUtils.getFilterQuery(
    UserSchema.schema,
    filter,
    page,
    pageSize,
    UserSchema.defaultSort
  );

  if (filterStr) {
    selectQuery += filterStr;
    countQuery += " " + filterStr;
  }

  if (paginationStr) {
    selectQuery += " " + paginationStr;
  }
  const result = await dbConfig.db.pool.request().query(selectQuery);
  let countResult = await dbConfig.db.pool.request().query(countQuery);

  let totalUser = 0;
  if (countResult.recordsets[0].length > 0) {
    totalUser = countResult.recordsets[0][0].totalItem;
  }
  let totalPage = Math.ceil(totalUser / pageSize); //round up
  const users = result.recordsets[0];
  return {
    Page: page,
    PageSize: pageSize,
    TotalPage: totalPage,
    TotalUser: totalUser,
    DataUsers: users,
  };
};

exports.clearAll = async () => {
  query = `delete ${UserSchema.schemaName}  DBCC CHECKIDENT ('[${UserSchema.schemaName} ]', RESEED, 1);`;
  let result = await dbConfig.db.pool.request().query(query);
  return result.recordsets;
};

exports.getUserById = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }

  const queryUser = `
  SELECT  * from ${UserSchema.schemaName} where ${UserSchema.schema.UserID.name} = @${UserSchema.schema.UserID.name}

 `;
  const queryTotalPrice = `

    select ${Order_DetailsSchema.schemaName}.${Order_DetailsSchema.schema.OrderID.name},
     sum(${Order_DetailsSchema.schemaName}.${Order_DetailsSchema.schema.Amount.name} * ${ProductSchema.schemaName}.${ProductSchema.schema.Price.name}) as TotalPrice
     from ${Order_DetailsSchema.schemaName}
     inner join ${OrdersSchema.schemaName} on ${OrdersSchema.schemaName}.${OrdersSchema.schema.OrderID.name} = ${Order_DetailsSchema.schemaName}.${Order_DetailsSchema.schema.OrderID.name}
     inner join ${ProductSchema.schemaName} on ${Order_DetailsSchema.schemaName}.${Order_DetailsSchema.schema.ProductID.name} = ${ProductSchema.schemaName}.${ProductSchema.schema.ProductID.name}
     where ${OrdersSchema.schemaName}.${OrdersSchema.schema.PayIn.name} is not null and ${OrdersSchema.schemaName}.${OrdersSchema.schema.UserID.name} = @${UserSchema.schema.UserID.name}
     group by ${Order_DetailsSchema.schemaName}.${Order_DetailsSchema.schema.OrderID.name}
  `;

  let resultUser = await dbConfig.db.pool
    .request()
    .input(UserSchema.schema.UserID.name, UserSchema.schema.UserID.sqlType, id)
    .query(queryUser);
  let resultTotalPrice = await dbConfig.db.pool
    .request()
    .input(UserSchema.schema.UserID.name, UserSchema.schema.UserID.sqlType, id)
    .query(queryTotalPrice);
  let totalPrice = 0;
  if (resultTotalPrice.recordset.length != 0) {
    totalPrice = resultTotalPrice.recordset[0].TotalPrice;
  }
  const result = {
    ...resultUser.recordset[0],
    TotalPrice: totalPrice,
  };
  if (resultUser.recordset.length > 0) {
    return new DTOUserCustomize(result);
  }
  return null;
};

exports.getUserByUserName = async (username) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let result = await dbConfig.db.pool
    .request()
    .input(
      UserSchema.schema.UserName.name,
      UserSchema.schema.UserName.sqlType,
      username
    )
    .query(
      `SELECT * from ${UserSchema.schemaName} where ${UserSchema.schema.UserName.name} = @${UserSchema.schema.UserName.name}`
    );

  if (result.recordsets[0].length > 0) {
    return new DTOUser(result.recordsets[0][0]);
  }

  return null;
};

exports.getUserByEmail = async (username) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  let result = await dbConfig.db.pool
    .request()
    .input(
      UserSchema.schema.Email.name,
      UserSchema.schema.Email.sqlType,
      username
    )
    .query(
      `SELECT * from ${UserSchema.schemaName} where ${UserSchema.schema.Email.name} = @${UserSchema.schema.Email.name}`
    );
  return result.recordsets[0][0];
};

exports.updateUserById = async (id, updateInfo) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  if (!updateInfo) {
    throw new Error("Invalid input param");
  }
  //updateInfo = UserSchema.validateData(updateInfo);
  if (updateInfo.Password) {
    updateInfo.Password = await bcrypt.hash(updateInfo.Password, 10);
  }
  // console.log(updateInfo);
  let query = `update ${UserSchema.schemaName} set`;
  const {request, updateStr} = dbUtils.getUpdateQuery(
    UserSchema.schema,
    dbConfig.db.pool.request(),
    updateInfo
  );
  if (!updateStr) {
    throw new Error("Invalid update param");
  }
  request.input(
    `${UserSchema.schema.UserID.name}`,
    UserSchema.schema.UserID.sqlType,
    id
  );
  query +=
    " " +
    updateStr +
    ` where ${UserSchema.schema.UserID.name} = @${UserSchema.schema.UserID.name}`;
  let result = await request.query(query);
  return result.recordsets;
};

exports.getUserByOrderID = async (orderId) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  const query = `
  select u.* from ${UserSchema.schemaName} u
  inner join ${OrdersSchema.schemaName} o on u.${UserSchema.schema.UserID.name} = o.${OrdersSchema.schema.UserID.name}
  where o.${OrdersSchema.schema.OrderID.name} = @${OrdersSchema.schema.OrderID.name}
  `;
  const result = await dbConfig.db.pool
    .request()
    .input(
      OrdersSchema.schema.OrderID.name,
      OrdersSchema.schema.OrderID.sqlType,
      orderId
    )
    .query(query);
  return result.recordset[0];
};

exports.deleteUserById = async (id) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }

  let request = dbConfig.db.pool.request();
  let result = await request
    .input(
      `${UserSchema.schema.UserID.name}`,
      UserSchema.schema.UserID.sqlType,
      id
    )
    .query(
      `delete ${UserSchema.schemaName} where ${UserSchema.schema.UserID.name} = @${UserSchema.schema.UserID.name}`
    );
  return result.recordsets;
};

exports.deleteMultipleUserById = async (idList, payload) => {
  if (!dbConfig.db.pool) {
    throw new Error("Not connected to db");
  }
  for (let i = 0; i < idList.length; i++) {
    UserSchema.schema.UserID.validate(idList[i]);
  }
  const usersQuery = `select UserID,AuthID from Users where UserID in (${idList.join(
    ","
  )})`;
  let request = dbConfig.db.pool.request();
  const resultUsersQuery = await request.query(usersQuery);

  const arrUsers = resultUsersQuery.recordsets[0];
  const checkAuth = arrUsers.some((x) => x.AuthID <= payload.AuthID);
  if (arrUsers.length != idList.length || checkAuth) {
    throw new Error("Fail!");
  }
  const deleteStr = dbUtils.getDeleteQuery(UserSchema, idList);
  let result = await request.query(
    `DELETE FROM ${UserSchema.schemaName} WHERE ${UserSchema.schema.UserID.name} ${deleteStr}`
  );
  return result.recordset;
};

exports.userSignUp = async (dto) => {
  let user = await this.getUserByEmail(dto.Email);
  if (user) {
    // console.log(user);
    throw new Error("User email used!");
  }
  user = await this.getUserByUserName(dto.UserName);
  if (user) {
    // console.log(user);
    throw new Error("User name used!");
  }
  const passEndcode = await bcrypt.hash(dto.Password, 10);
  dto.Password = passEndcode;
  await this.insertUser(dto);
  const u = await this.getUserByUserName(dto.UserName);
  await OrderDAO.createNewOrder(u.UserID);
  return u;
};

exports.changePassword = async (payload) => {
  const {UserID, OldPassword, NewPassword} = payload;
  const user = await this.getUserById(UserID);

  if (!user) {
    throw new Error("User not found!");
  }
  // const oldPassEncode = await bcrypt.hash(OldPassword, 10);
  const check = await bcrypt.compare(OldPassword, user.Password);

  if (!check) {
    throw new Error("Old password is not correct!");
  }

  const result = await this.updateUserById(UserID, {Password: NewPassword});
  return result;
};
