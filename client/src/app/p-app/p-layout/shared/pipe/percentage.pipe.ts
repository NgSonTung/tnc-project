import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
    name: 'percentage'
})

export class PercentagePipe implements PipeTransform {
    transform(value: string): string {
        // Assuming value is a string in the format '0,1'
        console.log(parseFloat(value) * 100);
        const convertValue = parseFloat(value) * 100;
        const percentageString = convertValue.toString() + '%';
        return percentageString;
    }
}