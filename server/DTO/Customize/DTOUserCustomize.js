const DTOUser = require("../../DTO/Default/DTOUser");

module.exports = class DTOUserCustomize extends DTOUser {
  constructor(data) {
    super(data);
    this.TotalPrice = data.TotalPrice;
  }
};
