import { Component, Input, OnInit, SkipSelf } from '@angular/core';
import { CartService } from '../../shared/services/cart.service';
import { Router } from '@angular/router';
import { DTOOrder } from '../../shared/dto/DTOOrder';
import { StorageService } from '../../shared/services/storage.service';
import { ProductService } from '../../shared/services/product.service';
import { Subject, takeUntil } from 'rxjs';
import { OrderService } from '../../shared/services/order.service';

@Component({
  selector: 'app-cart',
  templateUrl: './cart.component.html',
  styleUrls: ['./cart.component.scss'],
})
export class CartComponent implements OnInit {
  productList = [];
  ngUnsubscribe = new Subject<void>();
  total: number = 0;
  @Input() checkout: boolean = false;

  constructor(
    @SkipSelf() private productService: ProductService,
    private storageService: StorageService,
    private router: Router,
    private cartService: CartService,
    private orderService: OrderService
  ) {}

  ngOnInit(): void {
    this.getOrders();
  }

  deleteItem(product) {
    let orders = this.storageService.getOrders();
    const user = this.storageService.getUser();
    if (user.UserID) {
      // update db
      const order = {
        Amount: 0,
        OrderID: orders.orderId,
        ProductID: product.ProductID,
      };
      this.orderService.updateData(order).subscribe((res) => {});
    }

    // update session
    const productIndexToUpdate = orders.orders.findIndex(
      (order) => order.ProductID === product.ProductID
    );
    orders.totalAmount =
      orders.totalAmount - orders.orders[productIndexToUpdate].Amount;
    orders.orders[productIndexToUpdate].Amount = 0;
    orders.orders = orders.orders.filter(
      (item) => item.ProductID !== product.ProductID
    );

    this.storageService.saveOrders2(orders);
    this.getOrders();
  }

  increaseItem(product) {
    const updatedAmount = product.Amount + 1;
    if (updatedAmount <= product.Stock) {
      let orders = this.storageService.getOrders();
      const user = this.storageService.getUser();
      if (user.UserID) {
        // update db
        const order = {
          Amount: updatedAmount,
          OrderID: orders.orderId,
          ProductID: product.ProductID,
        };
        this.orderService.updateData(order).subscribe((res) => {});
      }

      // update session
      const productIndexToUpdate = orders.orders.findIndex(
        (order) => order.ProductID === product.ProductID
      );
      orders.orders[productIndexToUpdate].Amount = updatedAmount;

      orders.totalAmount = orders.totalAmount + 1;

      this.storageService.saveOrders2(orders);
      this.getOrders();
    }
  }

  decreaseItem(product) {
    const updatedAmount = product.Amount - 1;
    let orders = this.storageService.getOrders();
    if (updatedAmount >= 0) {
      const user = this.storageService.getUser();
      if (user.UserID) {
        //update db
        const order = {
          Amount: updatedAmount,
          OrderID: orders.orderId,
          ProductID: product.ProductID,
        };
        this.orderService.updateData(order).subscribe((res) => {});
      }

      // update session
      const productIndexToUpdate = orders.orders.findIndex(
        (order) => order.ProductID === product.ProductID
      );
      orders.orders[productIndexToUpdate].Amount = updatedAmount;
      if (updatedAmount == 0) {
        orders.orders = orders.orders.filter(
          (item) => item.ProductID !== product.ProductID
        );
      }

      orders.totalAmount = orders.totalAmount - 1;

      this.storageService.saveOrders2(orders);
      this.getOrders();
    } else {
      return;
    }
  }

  getOrders() {
    const orders = this.storageService.getOrders().orders;
    let total = 0;
    orders.forEach((product) => {
      total += product.Price * product.Amount;
      this.getProductImage(product.Image)
        .pipe(takeUntil(this.ngUnsubscribe))
        .subscribe((res) => {
          product.ImageSrc = res.Data.Base64;
        });
    });
    this.productList = orders;
    this.total = total;
  }

  getProductImage(imageName: string) {
    return this.productService.getProductImage(imageName);
  }

  getTotalProducts() {
    const amount = this.storageService.getOrders().totalAmount;
    return amount ? amount : 0;
  }

  redirectToCheckout() {
    this.router.navigateByUrl('/checkout');
  }

  onCloseCartPopUp() {
    this.cartService.onToggleCartPopUpState(false);
  }
}
