# Zadanie 2
## Opis zadania
Opracowany został pipeline w oparciu o GitHub Actions, budujący obraz kontenera na podstawie isniejących elementów a następnie przesyłający  go do publicznego rejestru kontenerów `ghcr.io`
## Spełniono podczas wykonania następujące warunki:
- Wsparcie dwóch architektur:  `linux/arm64` oraz `linux/amd64`
```yml
 - name: Build and push image
        id: build-and-push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
```
- Wysyłanie i pobieranie danych cache (`registry` -> `registry` w trybie `max`) oraz ich przechowywanie w publicznym repozytorium DockerHub
```yml
env:
  IMAGE_NAME: ghcr.io/${{ github.repository }}
  CACHE_REPO: docker.io/${{ secrets.DOCKERHUB_USERNAME }}/cache
.
.
.
  tags: |
            ${{ env.IMAGE_NAME }}:latest
            ${{ env.IMAGE_NAME }}:${{ github.sha }}
          cache-from: type=registry,ref=${{ env.CACHE_REPO }}:buildcache
          cache-to: type=registry,ref=${{ env.CACHE_REPO }}:buildcache,mode=max
```
- Wykonanie testu CVE (w oparciu o skaner Trivy) który blokuje przesyłanie obrazów zawierających luki o krytycznym lub wysokim stopniu zagrożenia
```yml
 - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.IMAGE_NAME }}:latest
          format: 'table'
          exit-code: '1'
          ignore-unfixed: true
          vuln-type: 'os,library'
          severity: 'CRITICAL,HIGH'
```
## Opis sposobów tagowania obrazów i danych cache
### Tagowanie obrazów
W pipeline przyjęto podwójne tagowanie obrazów kontenerowych:
- `latest` — odwołuje się do najnowszej wersji aplikacji znajdującej się w gałęzi `main`.
- `${{ github.sha }}` — identyfikator commit SHA, który pozwala na jednoznaczne powiązanie obrazu z konkretnym stanem kodu źródłowego.
Dzięki temu możliwe jest zarówno
- szybkie odniesienie się do aktualnej wersji (`latest`),
- jak i precyzyjne śledzenie wersji w historii (`sha`), co ułatwia debugowanie i audyt zmian.
  
Źródło: [Docker Tagging Best Practices](https://docs.docker.com/reference/cli/docker/image/tag/)
### Tagowanie danych cache
Dla cache warstwy build-a zastosowano:
- `ref=${{ env.CACHE_REPO }}:buildcache` — zarówno do `cache-from`, jak i `cache-to`, w trybie `mode=max`.
Zastosowanie dedykowanego repozytorium cache na DockerHub umożliwia:
- ponowne wykorzystanie wcześniej zbudowanych warstw, co znacznie skraca czas budowania obrazu,
- dzielenie cahce miedzy build-ami i platformami (multi-arch)
Tryb `mode=max` zapewnia maksymalne wykorzystanie dostępnego cache.

Źródło: [Docker Buildkit Catching with GitHub Actions](https://docs.docker.com/build/cache/backends/registry/)
