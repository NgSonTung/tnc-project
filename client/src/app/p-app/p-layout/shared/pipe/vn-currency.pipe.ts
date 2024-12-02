import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'vnCurrency',
})
export class VnCurrencyPipe implements PipeTransform {
  transform(value: number): string {
    if (value == null || isNaN(value)) return '';

    const parts = value.toFixed(0).toString().split('.');

    const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');

    return `${integerPart} đ${parts[1] ? '.' + parts[1] : ''}`;
  }
}
