import { Component, OnInit } from '@angular/core';

import { OAuthService } from 'angular-oauth2-oidc';

import { Studies } from '../typescript-angular-client/model/studies';

import { ReportService } from '../typescript-angular-client/api/report.service';


@Component({
  selector: 'app-report-multiple-location-gps',
  providers: [ReportService],
  templateUrl: './report-multiple-location-gps.component.html',
  styleUrls: ['./report-multiple-location-gps.component.scss']
})
export class ReportMultipleLocationGpsComponent implements OnInit {

  studies: Studies;

  constructor(private reportService: ReportService, private oauthService: OAuthService) { }

  ngOnInit() {

    this.reportService.multipleLocationGPS().subscribe(
      (studies) => {
        this.studies = studies;
      }
    )
  }

}
