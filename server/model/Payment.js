const ModelSchemaValidator = require("./ModelSchemaValidator");
const ModelSchema = require("./ModelSchema");
const sql = require("mssql");
const PaymentSchema = new ModelSchema(
  {
    PaymentID: new ModelSchemaValidator({
      name: "PaymentID",
      sqlType: sql.Int,
    }),
    PaymentName: new ModelSchemaValidator({
      name: "PaymentName",
      sqlType: sql.NVarChar,
    }),
    PaymentType: new ModelSchemaValidator({
      name: "PaymentType",
      sqlType: sql.NVarChar,
    }),

    CreatedAt: new ModelSchemaValidator({
      name: "CreatedAt",
      sqlType: sql.DateTime,
      default: new Date().toISOString(),
      require: true,
    }),
  },
  "Payment",
  "CreatedAt"
);

module.exports = PaymentSchema;
