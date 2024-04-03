import {Component} from '@angular/core';
import {CommonModule} from "@angular/common";
import {RouterLink, RouterOutlet} from "@angular/router";
import {HttpClientModule} from "@angular/common/http";
import {MatchService} from "../services/match.service";
import {ActivatedRoute} from "@angular/router";
import {OnInit} from "@angular/core";

@Component({
  selector: 'app-list-matchs-tournoi',
  standalone: true,
  imports: [CommonModule, RouterOutlet, HttpClientModule, RouterLink],
  providers: [MatchService],
  templateUrl: './list-matchs-tournoi.component.html',
})
export class ListMatchsTournoiComponent {
  nomTournoi: string = '';
  matchs: any[] = [];

  constructor(private serviceMatch: MatchService, private route: ActivatedRoute
  ) {
    this.route.params.subscribe(params => {
      this.nomTournoi = params['nomTournoi'];
    });
    this.rechercherMatchs()
  }


  rechercherMatchs(): void {
    this.serviceMatch.rechercherMatchsParNomTournoi(this.nomTournoi)
      .subscribe(matchs => {
        this.matchs = matchs;
      });
  }
}
