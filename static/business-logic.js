const TRANSLATION_KEYS = [
"word",
"root",
"meaning",
"language",
];

function tableDataFromTranslations(translations) {
  return {
    headers: TRANSLATION_KEYS.map(k => {
      return {html: k};
    }),
    rows: translations.map(t =>
      TRANSLATION_KEYS.map(k => {
        return {html: t[k], attr: [] };
      })
    )
  };
}
function renderTranslation(translation) {
  const tableData = tableDataFromTranslations(translation.translations);
  makeTable($(".translator-output--results-table"),tableData);
}
