const sql = require("mssql");
const ModelSchema = require("./ModelSchema");
const ModelSchemaValidator = require("./ModelSchemaValidator");
const StaticData = require("../utils/StaticData");

const UserSchema = new ModelSchema(
  {
    UserID: new ModelSchemaValidator({
      name: "UserID",
      sqlType: sql.Int,
    }),
    UserName: new ModelSchemaValidator({
      name: "UserName",
      sqlType: sql.VarChar,
      require: true,
    }),
    FullName: new ModelSchemaValidator({
      name: "FullName",
      sqlType: sql.NVarChar,
    }),
    Password: new ModelSchemaValidator({
      name: "Password",
      sqlType: sql.VarChar,
      require: true,
    }),
    AuthID: new ModelSchemaValidator({
      name: "AuthID",
      sqlType: sql.Int,
      require: true,
      default: StaticData.AUTH.Role.user,
    }),
    Email: new ModelSchemaValidator({
      name: "Email",
      require: true,
      sqlType: sql.VarChar,
      validator: function (val) {
        return String(val)
          .toLowerCase()
          .match(
            /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
          );
      },
    }),
    Point: new ModelSchemaValidator({
      name: "Point",
      sqlType: sql.Float,
      default: 0,
    }),
    Address: new ModelSchemaValidator({
      name: "Address",
      sqlType: sql.VarChar,
    }),
    Phone: new ModelSchemaValidator({
      name: "Phone",
      sqlType: sql.NVarChar,
    }),
    CreatedAt: new ModelSchemaValidator({
      name: "CreatedAt",
      sqlType: sql.DateTime,
      default: new Date().toISOString(),
      require: true,
    }),
  },
  "Users",
  "UserID"
);

module.exports = UserSchema;
