#ifndef DATA_PARSER_H
#define DATA_PARSER_H

#include <Arduino.h>

/**
 * Minimal comma-separated field parser used by the teleoperation firmware.
 * Matches the thesis interface: parseData(str, ','), getField(index).
 */
class DataParser {
 public:
  static const int MAX_FIELDS = 8;
  static const int MAX_FIELD_LEN = 32;

  DataParser();
  void parseData(const String& data, char delimiter);
  String getField(int index) const;
  int fieldCount() const { return _count; }

 private:
  char _fields[MAX_FIELDS][MAX_FIELD_LEN];
  int _count;
};

#endif
