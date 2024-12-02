import { CUSTOM_ELEMENTS_SCHEMA, NgModule ,NO_ERRORS_SCHEMA} from '@angular/core';
import { BoxProductComponent } from './boxProduct.component';
import { CommonModule, DecimalPipe } from '@angular/common';
import { BuyNowComponent } from './btnBuyNow/buyNow.component';
import { NgbRating } from '@ng-bootstrap/ng-bootstrap';
import { StarRatingModule } from 'angular-star-rating';

@NgModule({
  declarations :[BoxProductComponent,BuyNowComponent],
  imports :[DecimalPipe,NgbRating,CommonModule,StarRatingModule.forRoot()],
  schemas: [CUSTOM_ELEMENTS_SCHEMA, NO_ERRORS_SCHEMA],
  exports: [BoxProductComponent,BuyNowComponent],

})
export class BoxProductModule{}
