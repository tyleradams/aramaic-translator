const TRANSLATION_KEYS = {
  word: (a) => a.word,
  root: (a) => a.root,
  meaning: (a) => a.meaning,
  conjugation: (a) => Object.values(a.conjugation).join(", "),
  language: (a) => a.language,
};

function tableDataFromTranslations(translations) {
  return {
    headers: Object.keys(TRANSLATION_KEYS).map(k => {
      return {html: k};
    }),
    rows: translations.map(t =>
      Object.entries(TRANSLATION_KEYS).map(e => {
        return {html: e[1](t), attr: [] };
      })
    )
  };
}
function renderTranslation(translation) {
  const tableData = tableDataFromTranslations(translation.translations);
  makeTable($(".translator-output--results-table"),tableData);
}
