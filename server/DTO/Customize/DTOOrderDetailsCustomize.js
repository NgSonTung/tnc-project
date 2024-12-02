const DTOProductCustomize = require("./DTOProductCustomize");

module.exports = class DTOOrderDetailsProductCustomize extends (
  DTOProductCustomize
) {
  constructor(data) {
    super(data);
    this.OrderID = data.OrderID ?? null;
    this.Amount = data.Amount ?? null;
  }
};
