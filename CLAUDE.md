# Navegación Espacial en Personas con Discapacidad Visual

## Descripcion del proyecto

Artículo de investigación empírica titulado **"Cognición corporeizada y navegación espacial sin visión: El rol de las acciones motoras en la integración de trayectoria en personas con discapacidad visual"**.

Estudio cuasi-experimental (diseño factorial mixto 2x2x2x4) que explora cómo la experticia en navegación no visual modula la ponderación e integración de distintas claves sensoriales (kinestésicas-vestibulares, táctiles y de acción) durante tareas de integración de trayectoria. Compara el desempeño de personas con discapacidad visual adquirida (DV, n=15) frente a personas videntes con ojos vendados (NDV, n=13) usando el paradigma de completación de triángulos.

**Autores:** Mateo Belalcázar y Yenny Otálora.

## Afiliación institucional

- **Afiliación:** Facultad de Psicología, Universidad del Valle, Cali, Colombia.
- **Reclutamiento:** Hospital Universitario del Valle (HUV), Colombia.

## Revista objetivo

**Universitas Psychologica** — Pontificia Universidad Javeriana.
- Máximo 8000 palabras (incluyendo citas, tablas, figuras y referencias).
- Formato APA 7a edición.
- Resumen: 120-150 palabras (español e inglés).
- 3-6 palabras clave (cada una < 4 palabras).
- Fuente Times New Roman 12pt, interlineado 2.0, tamaño carta, márgenes 2.5cm.
- Figuras en archivos independientes (TIF/JPG/PNG, mínimo 300 dpi).

## Estructura del repositorio

```
├── CLAUDE.md                          # Este archivo
├── manuscrito/                        # Documento LaTeX
│   ├── main.tex                       # Archivo principal del manuscrito
│   ├── referencias.bib                # Bibliografía BibTeX (33 entradas, 26 citadas)
│   └── figuras/                       # Copias de figuras para compilación LaTeX
├── datos/                             # Datos experimentales
│   ├── datos 26_06_2024.xlsx          # Base de datos principal
│   ├── datos 26_06_2024 - copia.xlsx  # Copia de respaldo
│   ├── Posiciones_cada_tres_pasos.xlsx # Coordenadas XY paso a paso (ver sección abajo)
│   ├── Modalidad_x_forma.xlsx         # Datos cruzados: modalidad × forma
│   ├── Modalidad_x_tamaño.xlsx        # Datos cruzados: modalidad × tamaño
│   └── Modalidad_sensorial.xlsx       # Datos por modalidad sensorial
├── analisis/                          # Scripts y productos del análisis
│   ├── analisis_completo.py           # Script Python del análisis estadístico principal
│   ├── analisis_trayectorias.py       # Script Python del análisis de trayectorias paso a paso
│   ├── resultados_completos.txt       # Output completo del análisis
│   ├── guia_resultados.md             # Guía de resultados para escritura
│   └── literatura_actualizada.md      # Literatura 2020-2025 compilada
├── figuras/                           # Figuras originales (PNG 300 dpi)
│   ├── fig1_interaction_CE_MS.png     # Interacción CE × MS (barras con IC)
│   ├── fig2_individual_trajectories.png # Trayectorias individuales (puntos de llegada)
│   ├── fig3_absolute_vs_signed.png    # Error absoluto vs con signo
│   ├── fig4_variability.png           # Variabilidad intra-participante
│   ├── fig5_error_direction.png       # Sesgo direccional (violin plots)
│   ├── fig6_compensation_index.png    # Índice de compensación
│   ├── fig7_correlation_years.png     # Correlación años de ceguera vs error
│   ├── fig8_qq_residuals.png          # QQ plot de residuos
│   ├── fig9_trajectories_reconstructed.png  # Trayectorias reconstruidas paso a paso (2×4 panel)
│   ├── fig10_path_efficiency.png      # Eficiencia de trayectoria (violin + barras)
│   ├── fig11_lateral_deviation.png    # Desviación lateral sobre progreso de trayectoria
│   └── fig12_heading_consistency.png  # Evolución del error de rumbo por waypoint
└── docs_originales/                   # Versiones Word anteriores
    ├── Navegación ciegos.docx         # Versión principal (~julio 2025)
    ├── Navegación ciegos - abril 2025 - Mateo.docx
    ├── Criterios revista.docx         # Guía para autores de Universitas Psychologica
    └── Libro1.xlsx                    # Datos auxiliares
```

## Diseño experimental

### Variables independientes
- **Condición de experticia (CE):** DV (discapacidad visual adquirida) vs NDV (sin discapacidad visual) — factor inter-sujeto.
- **Organización por forma (OF):** Triángulos agudos (<45°) vs obtusos (>90°) — factor intra-sujeto.
- **Organización por tamaño (OT):** Distancia de retorno 2m vs 4m — factor intra-sujeto.
- **Modalidad sensorial (MS):** 4 niveles — factor intra-sujeto.
  1. Kinestésica-vestibular (sin objetos ni acciones, línea base)
  2. Tacto pasivo (tocar objetos sin usarlos)
  3. Interacción funcional (usar objetos)
  4. Control (acciones en el aire, sin objetos)

### Variables dependientes
- **Error de posición con signo (E.A):** Distancia en cm entre punto de origen y punto alcanzado (+ = sobreestimación, - = subestimación).
- **Error de estimación angular:** Diferencia en grados entre dirección estimada y dirección ideal.
- **Métricas de trayectoria (nuevas):** Eficiencia de trayectoria, desviación lateral, error de rumbo.

### Análisis estadístico
- Software: Python 3.11 (pingouin, scipy, statsmodels).
- ANOVA de medidas repetidas 2x2x2x4 (modelo completo).
- ANOVA de medidas repetidas 2x4 (CE x MS, colapsando OF y OT).
- Comparaciones post hoc con ajuste de Bonferroni.
- Análisis complementarios: error absoluto, sesgo direccional, variabilidad, análisis bayesiano, ART ANOVA.
- Análisis de trayectorias: eficiencia de ruta, desviación lateral, evolución del error de rumbo.

## Hallazgos principales

1. El grupo DV mostró mayor precisión y consistencia que el grupo NDV.
2. Interacción significativa CE × MS (F(3,78)=4.317, p=.007, η²p=.142): la modalidad sensorial afecta diferencialmente a cada grupo.
3. El grupo NDV mejoró significativamente en la condición Control (acciones en el aire), igualando al grupo DV (d=0.03).
4. La interacción opera sobre el sesgo direccional (error con signo), no sobre la precisión total (error absoluto: interacción p=.322).
5. El grupo DV no muestra sesgo en ninguna modalidad; el NDV sobreestima significativamente solo en cinestésica (d=0.97).
6. La información geométrica (forma, tamaño) no produjo interacciones significativas de orden superior.
7. El error de estimación angular no mostró interacciones significativas entre grupos.

## Datos de trayectorias paso a paso

### Archivo: `datos/Posiciones_cada_tres_pasos.xlsx`

Coordenadas XY de cada participante registradas cada 3 pasos durante el segmento de retorno de la completación de triángulos.

- **32 hojas:** 28 hojas individuales (una por participante) + hojas de resumen.
- **Coordenadas:** Rejilla 2D, cada baldosa ≈ 25 cm. Convertir a cm: coord × 25.
- **Origen (target):** Posición de rejilla (5, 15) = (125 cm, 375 cm).
- **Inicio:** (5, 8) para triángulos de 2m; (5, 1) para triángulos de 4m.
- **16 ensayos por participante** (2 formas × 2 tamaños × 4 modalidades).
- **3-7 waypoints** por ensayo según la longitud de la trayectoria.

### IMPORTANTE: Prefijos de hojas invertidos
- Hojas "PV" = grupo NDV (videntes, NO discapacidad visual).
- Hojas "PN" y "PM" = grupo DV (discapacidad visual).
- La hoja "Rejilla agrupados" usa: Grupo 1 = DV, Grupo 2 = NDV.

### Hallazgos del análisis de trayectorias (fig9-fig12)

**Resultados significativos a nivel global (t-tests):**
- Desviación lateral: DV 29.4 cm vs NDV 40.9 cm (d=-0.40, p<.001)
- Error de rumbo: DV 28.2° vs NDV 35.5° (d=-0.36, p<.001)
- Error final: DV 70.3 cm vs NDV 106.4 cm (d=-0.60, p<.001)

**ANOVAs mixtos 2(CE) × 4(MS) — ninguna interacción significativa:**
- Eficiencia de trayectoria: interacción p=.073 (tendencia marginal)
- Desviación lateral: interacción p=.293
- Error de rumbo: interacción p=.124

**Hallazgos cualitativos relevantes:**
1. El error de heading se acumula progresivamente (de ~20° a >60°) → navegación en lazo abierto.
2. El grupo DV mantiene heading más estable a lo largo de la trayectoria.
3. Paradoja de eficiencia: NDV en Acción camina trayectorias más rectas (d=-0.47) pero con peor precisión final → caminan recto hacia el lugar equivocado.
4. Fig9 (trayectorias reconstruidas) es visualmente muy informativa y podría reemplazar fig2.

## Marco teórico clave

- **Cognición corporeizada** (Shapiro, 2019; Wilson, 2002) — marco principal del manuscrito
- Integración de trayectoria y mapas cognitivos (O'Keefe & Nadel, 1978; Loomis et al., 2012)
- Integración multisensorial bayesiana (Loomis et al., 2012; Zhou & Gu, 2022)
- Simulación motora (Jeannerod, 2001)
- Modelo convergente de cognición espacial sin visión (Giudice, 2018)
- Plasticidad cross-modal en ceguera (Bleau et al., 2022; Chebat et al., 2020)

## Estado del manuscrito

- **main.tex:** Completo (~5,500 palabras). Secciones: Resumen ES/EN, Introducción, Método, Resultados, Discusión, Conclusiones.
- **referencias.bib:** 33 entradas, 26 citadas.
- **Figuras en Resultados:** 4 figuras (interacción CE×MS, trayectorias individuales, sesgo direccional, error absoluto vs con signo) + 1 tabla descriptiva.
- **Compila limpio:** pdflatex + biber sin errores (26 páginas).
- **Pendiente:** Evaluar inclusión de datos de trayectorias paso a paso (fig9-fig12).
