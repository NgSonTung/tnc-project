module.exports = class DTOProduct {
  constructor(data) {
    this.ProductID = data.ProductID;
    this.Stock = data.Stock;
    this.Name = data.Name;
    this.Favorite = data.Favorite;
    this.CategoryID = data.CategoryID;
    this.Price = data.Price;
    this.BrandID = data.BrandID;
    this.Image = data.Image;
    this.Sale = data.Sale;
    this.Description = data.Description;
    this.StatusID = data.StatusID;
    if (!data.CreatedAt) data.CreatedAt = new Date().toISOString();
    this.CreatedAt = data.CreatedAt;
  }
};
