#include "DataParser.h"

DataParser::DataParser() : _count(0) {
  for (int i = 0; i < MAX_FIELDS; i++) {
    _fields[i][0] = '\0';
  }
}

void DataParser::parseData(const String& data, char delimiter) {
  _count = 0;
  int start = 0;
  const int len = data.length();

  for (int i = 0; i <= len && _count < MAX_FIELDS; i++) {
    if (i == len || data.charAt(i) == delimiter) {
      int fieldLen = i - start;
      if (fieldLen >= MAX_FIELD_LEN) {
        fieldLen = MAX_FIELD_LEN - 1;
      }
      for (int j = 0; j < fieldLen; j++) {
        _fields[_count][j] = data.charAt(start + j);
      }
      _fields[_count][fieldLen] = '\0';
      _count++;
      start = i + 1;
    }
  }
}

String DataParser::getField(int index) const {
  if (index < 0 || index >= _count) {
    return String("");
  }
  return String(_fields[index]);
}
