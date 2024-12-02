import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'salePricePipe',
})

  export class SalePricePipe implements PipeTransform {
    transform(price: number, percent: string ): number {
        const convertedPercent: any = parseFloat(percent);
        const saleprice = price - price * convertedPercent;
        return saleprice;
    }
}
  