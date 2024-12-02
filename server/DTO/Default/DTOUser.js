module.exports = class DTOUser {
  constructor(data) {
    this.UserID = data.UserID;
    this.UserName = data.UserName;
    this.FullName = data.FullName;
    this.Password = data.Password;
    this.AuthID = data.AuthID;
    this.Email = data.Email;
    this.Point = data.Point;
    this.Address = data.Address;
    this.Phone = data.Phone;
    if (!data.CreatedAt) data.CreatedAt = new Date().toISOString();
    this.CreatedAt = data.CreatedAt;
  }
};
