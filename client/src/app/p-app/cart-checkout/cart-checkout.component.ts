import { Component, OnDestroy, OnInit, SkipSelf } from '@angular/core';
import { LayoutAPIService } from '../p-layout/shared/services/layout-api.service';
import { Subject, filter, map, takeUntil } from 'rxjs';
import { DTOProduct } from '../product/shared/dto/DTOProduct.dto';

@Component({
  selector: 'app-cart-checkout',
  templateUrl: './cart-checkout.component.html',
  styleUrls: ['./cart-checkout.component.scss'],
})
export class CartCheckoutComponent implements OnInit, OnDestroy {
  sliderProducts: DTOProduct[] = [];

  private unsubscription$ = new Subject<void>();

  constructor(@SkipSelf() private layoutAPIService: LayoutAPIService) { }

  ngOnInit(): void {
    this.GetListFilteredProduct();
  }

  GetListFilteredProduct() {
    this.layoutAPIService.GetProducts().pipe(
      filter(res => res.length > 0),
      takeUntil(this.unsubscription$)
    ).subscribe(
      res => this.sliderProducts = [...res.slice(0, 15)]
    )
  }

  ngOnDestroy(): void {
    this.unsubscription$.next();
    this.unsubscription$.complete();
  }
}
