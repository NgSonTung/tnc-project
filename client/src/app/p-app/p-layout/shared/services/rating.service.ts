import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { DTORating } from '../dto/DTORating';
import { DTOResponse } from '../dto/DTOResponse';

@Injectable({
  providedIn: 'root',
})
export class RatingService {
  constructor(private http: HttpClient) {
    console.log('rating service started');
  }

  getData(
    page: number,
    pageSize: number,
    filterStr: string
  ): Observable<DTOResponse> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());
    return this.http
      .get<DTOResponse>(`/api/v1/rating/${filterStr}`, {
        params,
      })
      .pipe(catchError(this.handleError));
  }

  getDataById(id: number): Observable<DTOResponse> {
    return this.http
      .get<DTOResponse>(`/api/v1/rating/${id}`)
      .pipe(catchError(this.handleError));
  }

  createData(rating: DTORating): Observable<DTOResponse> {
    return this.http
      .post<DTOResponse>('/api/v1/rating', rating)
      .pipe(catchError(this.handleError));
  }

  updateData(id: number, rating: DTORating): Observable<DTOResponse> {
    return this.http
      .patch<DTOResponse>(`/api/v1/rating/${id}`, rating)
      .pipe(catchError(this.handleError));
  }

  addRating(rating: any): Observable<DTOResponse> {
    return this.http
      .patch<DTOResponse>(`/api/v1/rating`, rating)
      .pipe(catchError(this.handleError));
  }

  deleteDataById(id: number): Observable<DTOResponse> {
    return this.http
      .delete<DTOResponse>(`/api/v1/rating/${id}`)
      .pipe(catchError(this.handleError));
  }

  private handleError(error: any) {
    console.error('An error occurred:', error);
    return throwError(
      () => new Error('Something went wrong. Please try again later.')
    );
  }
}
